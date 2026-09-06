import test from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { Ajv2020 } from "ajv/dist/2020.js";

test("the same six contracts accept/reject the same 12 fixtures in TypeScript", () => {
  const root = new URL("../../../shared-schemas/", import.meta.url);
  const ajv = new Ajv2020({ strict: true });
  let count = 0;
  for (const file of readdirSync(fileURLToPath(root)).filter(f => f.endsWith(".schema.json"))) {
    const name = file.replace(".schema.json", "");
    const schema = JSON.parse(readFileSync(new URL(file, root), "utf8"));
    const validate = ajv.compile(schema);
    for (const kind of ["valid", "invalid"]) {
      const example = JSON.parse(readFileSync(new URL(`examples/${name}.${kind}.json`, root), "utf8"));
      assert.equal(validate(example), kind === "valid", `${name}.${kind}`);
      count++;
    }
  }
  assert.equal(count, 12);
});
