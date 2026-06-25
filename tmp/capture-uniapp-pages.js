const fs = require('fs')
const path = require('path')

function findPlaywrightPackage() {
  const roots = [
    'D:/Node/node_cache/_npx',
    path.join(process.env.LOCALAPPDATA || '', 'npm-cache/_npx'),
  ].filter(Boolean)

  for (const root of roots) {
    if (!fs.existsSync(root))
      continue
    const stack = [root]
    while (stack.length) {
      const dir = stack.pop()
      for (const name of fs.readdirSync(dir)) {
        const full = path.join(dir, name)
        let stat
        try {
          stat = fs.statSync(full)
        }
        catch {
          continue
        }
        if (stat.isDirectory()) {
          if (full.replace(/\\/g, '/').endsWith('/node_modules/playwright') && fs.existsSync(path.join(full, 'index.js')))
            return full
          stack.push(full)
        }
      }
    }
  }
  throw new Error('playwright package not found in npx cache')
}

const { chromium } = require(findPlaywrightPackage())

async function main() {
  const pages = JSON.parse(fs.readFileSync('teacher_help_uniapp/src/pages.json', 'utf8')).pages.map(p => p.path)
  const outDir = 'tmp/uniapp-screens/all'
  fs.mkdirSync(outDir, { recursive: true })
  const browser = await chromium.launch()
  const context = await browser.newContext({
    viewport: { width: 393, height: 852 },
    deviceScaleFactor: 1,
    storageState: 'tmp/mock-login-storage.json',
  })
  const page = await context.newPage()
  const results = []
  for (const route of pages) {
    const url = `http://127.0.0.1:9000/#/${route}`
    const file = path.join(outDir, `${route.replace(/\//g, '__')}.png`)
    let text = ''
    let error = ''
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 })
      await page.waitForTimeout(1800)
      text = (await page.locator('body').innerText({ timeout: 5000 })).replace(/\s+/g, ' ').trim()
      await page.screenshot({ path: file })
    }
    catch (e) {
      error = e.message
    }
    results.push({
      route,
      file,
      loginLike: text.includes('请输入手机号') && text.includes('登录'),
      blankLike: text.length < 10,
      sample: text.slice(0, 120),
      error,
    })
  }
  await browser.close()
  fs.writeFileSync(path.join(outDir, 'results.json'), JSON.stringify(results, null, 2), 'utf8')
  console.log(JSON.stringify(results.map(({ route, loginLike, blankLike, sample, error }) => ({ route, loginLike, blankLike, sample, error })), null, 2))
}

main().catch((e) => {
  console.error(e)
  process.exit(1)
})
