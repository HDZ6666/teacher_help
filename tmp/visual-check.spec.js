const { test } = require('playwright/test')

test('inspect storage', async ({ page }) => {
  await page.setViewportSize({ width: 393, height: 852 })
  await page.goto('http://127.0.0.1:9000/#/pages/login/login', { waitUntil: 'networkidle' })
  const keys = await page.evaluate(() => Object.keys(localStorage).map(k => [k, localStorage.getItem(k)]))
  console.log(JSON.stringify(keys, null, 2))
})
