import { expect, test } from '@playwright/test'
import { analizar, imagen, simularApi } from './ayuda'

const RUTAS = ['/', '/acceso', '/registro', '/inicio', '/carga', '/resultados', '/comparacion', '/historial']

test.describe('cada pantalla', () => {
  for (const ruta of RUTAS) {
    test(`${ruta}: carga sin errores de consola`, async ({ page }) => {
      const errores = []
      page.on('pageerror', (e) => errores.push(e.message))
      page.on('console', (m) => m.type() === 'error' && errores.push(m.text()))
      await simularApi(page)
      await page.goto(ruta)
      await expect(page.locator('body')).toBeVisible()
      expect(errores).toEqual([])
    })
  }
})

test('flujo completo: cargar, analizar y ver la ROI con el aviso', async ({ page }) => {
  await simularApi(page)
  await analizar(page, [imagen('colon.png')])
  await expect(page).toHaveURL(/\/resultados\//)
  await expect(page.locator('.image-stage .roi-box')).toHaveCount(1)
  await expect(page.getByText(/no constituye|diagnóstico/i).first()).toBeVisible()
})

test('CF-02: una imagen rechazada no impide analizar las demás', async ({ page }) => {
  await simularApi(page)
  await analizar(page, [imagen('a.png'), imagen('mala.png', 'RECHAZAR'), imagen('c.png', 'c')])
  await expect(page).toHaveURL(/\/resultados\//)
  await expect(page.locator('.rejected-files')).toContainText('mala.png')
  await expect(page.locator('.rejected-files')).toContainText('Formato no admitido')
  await expect(page.getByText('1 de 2 imágenes')).toBeVisible()
})

test('la carga acepta como máximo 10 imágenes y no agrega BMP', async ({ page }) => {
  await page.goto('/carga')
  const once = Array.from({ length: 11 }, (_, i) => imagen(`i${i}.png`, 'x'.repeat(i)))
  await page.locator('input[type="file"]').setInputFiles([...once, { name: 'f.bmp', mimeType: 'image/bmp', buffer: Buffer.from('BM') }])
  await expect(page.locator('.remove-file')).toHaveCount(10)
})

test('CF-04: la comparación muestra original, máscara y superposición alineadas', async ({ page }) => {
  await simularApi(page)
  await analizar(page, [imagen('colon.png')])
  await expect(page).toHaveURL(/\/resultados\//)
  await page.goto('/comparacion')
  const fila = page.locator('.compare-row').first()
  await expect(fila.locator('.stage')).toHaveCount(3)
  const cajas = await fila.locator('.stage').evaluateAll((els) => els.map((e) => { const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)] }))
  expect(new Set(cajas.map(String)).size).toBe(1)
  await expect(fila.locator('img.overlay')).toBeVisible()
})

test('el historial se conserva al recargar y se puede reabrir', async ({ page }) => {
  await simularApi(page)
  await analizar(page, [imagen('colon.png')])
  await expect(page).toHaveURL(/\/resultados\//)
  await page.goto('/historial'); await page.reload()
  await expect(page.locator('.open-button')).toHaveCount(1)
  await page.locator('.open-button').click()
  await expect(page).toHaveURL(/\/resultados\//)
})

test('registro, sesión visible y cierre de sesión', async ({ page }) => {
  await simularApi(page)
  await page.goto('/registro')
  await page.locator('input[type="text"]').fill('Ana Ruiz')
  await page.locator('input[type="email"]').fill('ana@x.co')
  await page.locator('select[name="userType"]').selectOption('Profesional')
  await page.locator('input[type="password"]').nth(0).fill('ClaveSegura123')
  await page.locator('input[type="password"]').nth(1).fill('ClaveSegura123')
  await page.locator('input[type="checkbox"]').check()
  await page.getByRole('button', { name: /Crear mi cuenta/ }).click()
  await expect(page).toHaveURL(/\/inicio$/)
  await expect(page.locator('.account-name')).toHaveText('Ana R.')
  const almacenado = await page.evaluate(() => JSON.stringify({ ...localStorage }))
  expect(almacenado).not.toContain('ClaveSegura123')
  await page.locator('button[aria-controls="profile-dropdown"]').click()
  await page.locator('.logout-action').click()
  await expect(page).toHaveURL('http://localhost:4173/')
  await expect(page.getByText('Iniciar sesión')).toBeVisible()
})

test('una clave incorrecta muestra el error y no entra', async ({ page }) => {
  await simularApi(page)
  await page.goto('/acceso')
  await page.locator('input[type="email"]').fill('ana@x.co')
  await page.locator('input[type="password"]').fill('incorrecta')
  await page.getByRole('button', { name: /Entrar a mi cuenta/ }).click()
  await expect(page.getByRole('alert')).toHaveText('Correo o contraseña incorrectos.')
  await expect(page).toHaveURL(/\/acceso$/)
})

test('API caída: mensaje claro sin romper la pantalla', async ({ page }) => {
  await simularApi(page, 'caida')
  await analizar(page, [imagen('colon.png')])
  await expect(page.getByText('No se pudo completar el análisis')).toBeVisible()
  await expect(page.getByText(/No se pudo conectar/)).toBeVisible()
  await expect(page.getByRole('link', { name: 'Volver a cargar' })).toBeVisible()
})

test('API con error 500: muestra el mensaje en español', async ({ page }) => {
  await simularApi(page, 'error500')
  await analizar(page, [imagen('colon.png')])
  await expect(page.getByText('Ocurrió un error interno al procesar la imagen.')).toBeVisible()
})

test.describe('responsive en celular (375 px)', () => {
  test.use({ viewport: { width: 375, height: 812 } })
  for (const ruta of RUTAS) {
    test(`${ruta}: sin desplazamiento horizontal`, async ({ page }) => {
      await simularApi(page)
      await page.goto(ruta)
      const desborde = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)
      expect(desborde).toBeLessThanOrEqual(2)
    })
  }
})
