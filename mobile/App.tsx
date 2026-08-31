import { useRef, useState } from 'react'
import {
  ActivityIndicator,
  Image,
  Linking,
  Platform,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from 'react-native'
import { StatusBar } from 'expo-status-bar'
import { WebView } from 'react-native-webview'

declare const process: { env: Record<string, string | undefined> }

const HOSHIDORI_URL = process.env.EXPO_PUBLIC_HOSHIDORI_URL || 'https://hoshidori.netlify.app'
const configuredHost = (() => {
  try {
    return new URL(HOSHIDORI_URL).hostname
  } catch {
    return 'hoshidori.netlify.app'
  }
})()
const HOSHIDORI_HOSTS = new Set([
  configuredHost,
  'hoshidori.netlify.app',
  'hoshidori-67b44bed2d10.herokuapp.com',
])
const MERCHANT_PATHS = ['/shops/for-business', '/dashboard']

export default function App() {
  const webView = useRef<WebView>(null)
  const [reloadKey, setReloadKey] = useState(0)
  const [failed, setFailed] = useState(false)

  const shouldLoad = ({ url }: { url: string }) => {
    if (url === 'about:blank') return true
    try {
      const target = new URL(url)
      if (HOSHIDORI_HOSTS.has(target.hostname)) {
        if (MERCHANT_PATHS.some((path) => target.pathname.startsWith(path))) {
          void Linking.openURL(url)
          return false
        }
        return true
      }
      void Linking.openURL(url)
      return false
    } catch {
      return true
    }
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="light" />
      {failed ? (
        <View style={styles.error}>
          <Text style={styles.errorTitle}>ページを読み込めませんでした</Text>
          <Text style={styles.errorText}>通信状態を確認して、もう一度お試しください。</Text>
          <Pressable
            accessibilityRole="button"
            onPress={() => {
              setFailed(false)
              setReloadKey((current) => current + 1)
            }}
            style={styles.retry}
          >
            <Text style={styles.retryText}>再読み込み</Text>
          </Pressable>
        </View>
      ) : (
        <WebView
          key={reloadKey}
          ref={webView}
          source={{ uri: HOSHIDORI_URL }}
          style={styles.webView}
          containerStyle={styles.webViewContainer}
          sharedCookiesEnabled
          thirdPartyCookiesEnabled
          allowsBackForwardNavigationGestures
          pullToRefreshEnabled={Platform.OS === 'ios'}
          applicationNameForUserAgent="HOSHIDORI-iOS"
          onShouldStartLoadWithRequest={shouldLoad}
          onHttpError={({ nativeEvent }) => {
            if (nativeEvent.statusCode >= 500) setFailed(true)
          }}
          onError={() => setFailed(true)}
          startInLoadingState
          renderLoading={() => (
            <View style={styles.loading}>
              <Image
                source={require('./assets/splash-hoshidori.png')}
                style={styles.loadingLogo}
              />
              <ActivityIndicator color="#f43f5e" />
            </View>
          )}
        />
      )}
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#09090b',
  },
  webViewContainer: {
    flex: 1,
    backgroundColor: '#09090b',
  },
  webView: {
    flex: 1,
    backgroundColor: '#09090b',
  },
  loading: {
    position: 'absolute',
    top: 0,
    right: 0,
    bottom: 0,
    left: 0,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#09090b',
  },
  loadingLogo: {
    width: 96,
    height: 96,
    marginBottom: 18,
  },
  error: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 28,
    backgroundColor: '#09090b',
  },
  errorTitle: {
    color: '#fafafa',
    fontSize: 17,
    fontWeight: '700',
  },
  errorText: {
    marginTop: 8,
    color: '#71717a',
    fontSize: 13,
    textAlign: 'center',
  },
  retry: {
    marginTop: 22,
    paddingHorizontal: 22,
    paddingVertical: 11,
    borderRadius: 10,
    backgroundColor: '#f43f5e',
  },
  retryText: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '700',
  },
})
