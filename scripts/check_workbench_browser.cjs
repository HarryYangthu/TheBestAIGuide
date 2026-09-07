// Run from repository root after installing the browser-agent Playwright dependency.
const { chromium } = require('../10-Knowledge/13-application-engineering/05-code/browser-agent-typescript/node_modules/playwright');
const { spawn } = require('node:child_process');
const { mkdirSync } = require('node:fs');
const assert = require('node:assert/strict');
(async () => {
  const child = spawn(process.env.PYTHON || 'python', ['scripts/run_python.py', '-m', 'learning_workbench.server', '--port', '8766', '--directory', '.runs/browser-workbench'], { stdio: ['ignore', 'pipe', 'inherit'] });
  let browser;
  try {
    await new Promise((resolve, reject) => {
      const timer=setTimeout(()=>reject(Error('service startup timed out')),5000);
      child.once('exit',code=>{clearTimeout(timer);reject(Error(`service exited ${code}`));});
      child.stdout.once('data',()=>{clearTimeout(timer);resolve();});
    });
    browser = await chromium.launch({headless:true});
    const page = await browser.newPage({viewport:{width:1100,height:850}});
    const errors=[];page.on('pageerror',e=>errors.push(String(e)));
    await page.goto('http://127.0.0.1:8766');
    await page.locator('#create').click();
    await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('awaiting_approval'));
    await page.locator('#approve').click();
    await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('completed'));
    assert.match(await page.locator('#events').innerText(),/approval_required/);
    assert.match(await page.locator('#events').innerText(),/completed/);
    assert.notEqual(await page.locator('#result').innerText(),'null');
    mkdirSync('.runs/browser-workbench',{recursive:true});
    await page.screenshot({path:'.runs/browser-workbench/completed.png',fullPage:true});
    await page.locator('#create').click();
    await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('awaiting_approval'));
    await page.locator('#cancel').click();
    await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('cancelled'));
    await page.setViewportSize({width:390,height:844});
    // Stress long identifiers as well as the runner's actual Chinese font metrics.
    await page.addStyleTag({content:'#status{letter-spacing:2px}'});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({created:true,approved:true,completed:true,events_visible:true,cancelled:true,mobile_no_horizontal_overflow:true,page_errors:errors}));
  } finally {
    if(browser) await browser.close();child.kill();
  }
})().catch(e=>{console.error(e);process.exitCode=1;});
