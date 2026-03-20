/**
 * Cloudinary URL に変換パラメータを付与する
 * 非Cloudinary URL はそのまま返す
 *
 * @param {string|null} url - 画像URL
 * @param {object} opts - { w: width, h: height, f: format, q: quality }
 * @returns {string|null}
 */
export function cloudinaryUrl(url, opts = {}) {
  if (!url) return url
  // Cloudinary URL でなければそのまま返す
  if (!url.includes('res.cloudinary.com')) return url

  const { w, h, f = 'auto', q = 'auto' } = opts
  const parts = []
  if (w) parts.push(`w_${w}`)
  if (h) parts.push(`h_${h}`)
  parts.push(`f_${f}`)
  parts.push(`q_${q}`)
  parts.push('c_limit')

  const transform = parts.join(',')

  // /upload/ の直後に変換パラメータを挿入
  return url.replace('/upload/', `/upload/${transform}/`)
}

// プリセット
export const IMG_THUMB = { w: 200 }    // 一覧サムネイル
export const IMG_CARD = { w: 400 }     // カード画像
export const IMG_HERO = { w: 800 }     // ヒーロー画像
export const IMG_TINY = { w: 100 }     // 小サムネイル
