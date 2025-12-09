import { Camera, CameraResultType, CameraSource } from '@capacitor/camera'
import { Capacitor } from '@capacitor/core'

export const isNativePlatform = () => Capacitor.isNativePlatform()

export function dataUrlToFile(dataUrl, fileName = 'photo.jpg') {
  const parts = dataUrl.split(',')
  const mimeMatch = parts[0].match(/:(.*?);/)
  const mime = mimeMatch?.[1] || 'image/jpeg'
  const binary = atob(parts[1] || '')
  const array = new Uint8Array(binary.length)
  for (let i = 0; i < binary.length; i += 1) {
    array[i] = binary.charCodeAt(i)
  }
  return new File([array], fileName, { type: mime })
}

export async function pickImageFromLibrary(options = {}) {
  if (!isNativePlatform()) {
    throw new Error('not-native')
  }

  try {
    const photo = await Camera.getPhoto({
      source: CameraSource.Photos,
      resultType: CameraResultType.DataUrl,
      quality: options.quality ?? 85,
      correctOrientation: true,
      saveToGallery: false,
      // presentationStyleはiPhoneで問題を起こすため削除
      ...options,
    })

    if (!photo?.dataUrl) {
      throw new Error('写真を取得できませんでした')
    }

    const fileName = options.fileName || `photo-${Date.now()}.jpg`
    const file = dataUrlToFile(photo.dataUrl, fileName)

    return {
      file,
      previewUrl: photo.dataUrl,
    }
  } catch (err) {
    console.error('Camera.getPhoto error:', err)
    // より詳細なエラー情報を提供
    if (err.message && err.message.includes('User cancelled')) {
      throw new Error('キャンセルされました')
    }
    throw new Error(`写真の取得に失敗しました: ${err.message || '不明なエラー'}`)
  }
}
