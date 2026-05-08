import { App as AntdApp, ConfigProvider } from 'antd'
import { AppRouter } from './router'
import { appTheme } from './styles/theme'

function App() {
  return (
    <ConfigProvider theme={appTheme}>
      <AntdApp>
        <AppRouter />
      </AntdApp>
    </ConfigProvider>
  )
}

export default App
