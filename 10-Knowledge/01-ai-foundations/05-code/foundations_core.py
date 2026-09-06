"""Small, inspectable CPU teaching implementations; synthetic data only."""
from __future__ import annotations
import heapq
import math
import numpy as np


def mse_gradient(X, y, w):
    """X:(n,d), y:(n,), w:(d,). L=mean((Xw-y)^2)/2."""
    X, y, w = map(lambda z: np.asarray(z, dtype=float), (X, y, w))
    if X.ndim != 2 or y.shape != (X.shape[0],) or w.shape != (X.shape[1],):
        raise ValueError("Expected X:(n,d), y:(n,), w:(d,)")
    residual = X @ w - y
    return float(residual @ residual / (2 * len(y))), X.T @ residual / len(y)


def ridge_fit(X, y, lam=0.0):
    """Solve ||Xw-y||^2 + lam*||w||^2; intercept is column 0, unpenalized."""
    X, y = np.asarray(X, float), np.asarray(y, float)
    if lam < 0 or X.ndim != 2 or y.shape != (len(X),):
        raise ValueError("Invalid ridge inputs")
    penalty = np.eye(X.shape[1]) * math.sqrt(lam)
    penalty[0, 0] = 0
    return np.linalg.lstsq(np.vstack([X, penalty]), np.r_[y, np.zeros(X.shape[1])], rcond=None)[0]


def sigmoid(z):
    z = np.asarray(z, float)
    return np.exp(-np.logaddexp(0, -z))


def binary_nll(logits, labels, temperature=1.0):
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    z = np.asarray(logits, float) / temperature
    y = np.asarray(labels, float)
    return float(np.mean(np.logaddexp(0, z) - y * z))


def calibration_metrics(logits, labels, temperature=1.0, bins=5):
    """Binary top-label ECE: confidence=max(p,1-p); Brier uses positive-class p."""
    if bins < 1 or temperature <= 0:
        raise ValueError("bins and temperature must be positive")
    y = np.asarray(labels)
    p = sigmoid(np.asarray(logits) / temperature)
    confidence = np.maximum(p, 1-p)
    correct = (p >= .5) == y
    edges = np.linspace(.5, 1., bins+1)
    ece, rows = 0., []
    for i, (left, right) in enumerate(zip(edges[:-1], edges[1:])):
        mask = (confidence >= left) & ((confidence <= right) if i == bins-1 else (confidence < right))
        if mask.any():
            acc, conf = float(correct[mask].mean()), float(confidence[mask].mean())
            ece += mask.mean() * abs(acc-conf)
            rows.append((int(mask.sum()), acc, conf))
    return {"accuracy": float(correct.mean()), "nll": binary_nll(logits, labels, temperature),
            "brier": float(np.mean((p-y)**2)), "ece": float(ece), "bins": rows}


class Scalar:
    """Reverse-mode automatic differentiation for a scalar DAG.

    Backward resets every reachable gradient then accumulates every edge.
    This makes a shared node such as x*x work correctly.
    """
    def __init__(self, data, children=()):
        self.data, self.grad = float(data), 0.0
        self.children = tuple(children)
        self._backward = lambda: None

    def __add__(self, other):
        other = other if isinstance(other, Scalar) else Scalar(other)
        out = Scalar(self.data + other.data, (self, other))
        def backward():
            self.grad += out.grad
            other.grad += out.grad
        out._backward = backward
        return out
    __radd__ = __add__

    def __mul__(self, other):
        other = other if isinstance(other, Scalar) else Scalar(other)
        out = Scalar(self.data * other.data, (self, other))
        def backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = backward
        return out
    __rmul__ = __mul__

    def __neg__(self):
        return self * -1
    def __sub__(self, other):
        return self + (-other)
    def __rsub__(self, other):
        return -self + other

    def tanh(self):
        t = math.tanh(self.data)
        out = Scalar(t, (self,))
        def backward():
            self.grad += (1-t*t) * out.grad
        out._backward = backward
        return out

    def backward(self):
        ordered, seen = [], set()
        def visit(node):
            if node not in seen:
                seen.add(node)
                for child in node.children:
                    visit(child)
                ordered.append(node)
        visit(self)
        for node in ordered:
            node.grad = 0.
        self.grad = 1.
        for node in reversed(ordered):
            node._backward()


def train_xor(steps=1600, learning_rate=.1, seed=7):
    """2->4(tanh)->1 network, scalar autodiff, four synthetic XOR examples."""
    rng = np.random.default_rng(seed)
    w = [[Scalar(v) for v in row] for row in rng.normal(0, .8, (4, 2))]
    b = [Scalar(0) for _ in range(4)]
    v = [Scalar(x) for x in rng.normal(0, .8, 4)]
    c = Scalar(0)
    params = [p for row in w for p in row] + b + v + [c]
    samples = [([-1,-1],-1), ([-1,1],1), ([1,-1],1), ([1,1],-1)]
    def forward(x):
        hidden = [(sum(wi*xi for wi,xi in zip(row,x)) + bi).tanh() for row,bi in zip(w,b)]
        return sum(vi*hi for vi,hi in zip(v,hidden)) + c
    history = []
    for step in range(steps):
        errors = [forward(x)-y for x,y in samples]
        loss = sum(e*e for e in errors) * .25
        loss.backward()
        for p in params:
            p.data -= learning_rate * p.grad
        if step in (0,99,399,steps-1):
            history.append((step+1, loss.data))
    return history, [forward(x).data for x,_ in samples]


def astar(graph, start, goal, heuristic):
    """Nonnegative costs, reopen improved states; returns path,cost,expanded."""
    frontier, best, parent, expanded = [(heuristic(start), 0., start)], {start: 0.}, {}, 0
    while frontier:
        _, g, state = heapq.heappop(frontier)
        if g != best.get(state):
            continue
        expanded += 1
        if state == goal:
            path = [state]
            while state != start:
                state = parent[state]
                path.append(state)
            return path[::-1], g, expanded
        for nxt, cost in graph.get(state, []):
            if cost < 0:
                raise ValueError("A* requires nonnegative costs")
            candidate = g + cost
            if candidate < best.get(nxt, float('inf')):
                best[nxt], parent[nxt] = candidate, state
                heapq.heappush(frontier, (candidate+heuristic(nxt), candidate, nxt))
    raise ValueError("Goal unreachable")


def line_transition(state, action, length=5):
    """Move left(0)/right(1); enter rightmost terminal earns 1, otherwise 0."""
    if state == length-1:
        return state, 0., True
    nxt = min(length-1, max(0, state + (1 if action else -1)))
    done = nxt == length-1
    return nxt, float(done), done


def value_iteration(length=5, gamma=.9, tolerance=1e-12):
    if not 0 <= gamma < 1:
        raise ValueError("Discounted iteration requires 0 <= gamma < 1")
    values = np.zeros(length)
    for _ in range(10000):
        updated = values.copy()
        for state in range(length-1):
            candidates = []
            for action in (0,1):
                nxt, reward, done = line_transition(state, action, length)
                candidates.append(reward + gamma * (not done) * values[nxt])
            updated[state] = max(candidates)
        if np.max(abs(updated-values)) < tolerance:
            return updated
        values = updated
    raise RuntimeError("Iteration did not converge")


def q_learning(episodes=1500, length=5, gamma=.9, alpha=.2, epsilon=.25, seed=7):
    rng, q = np.random.default_rng(seed), np.zeros((length, 2))
    for _ in range(episodes):
        state = 0
        for _ in range(100):
            action = int(rng.integers(2)) if rng.random() < epsilon else int(np.argmax(q[state]))
            nxt, reward, done = line_transition(state, action, length)
            target = reward + gamma * (not done) * q[nxt].max()
            q[state, action] += alpha * (target-q[state, action])
            state = nxt
            if done:
                break
    return q
