import { ConfigProvider } from 'antd'
import { AppRouter } from './router'
import { appTheme } from './styles/theme'

function App() {
  return (
    <ConfigProvider theme={appTheme}>
      <AppRouter />
    </ConfigProvider>
  )
}

export default App
