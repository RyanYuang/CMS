import type { ThemeConfig } from 'antd'

export const appTheme: ThemeConfig = {
  token: {
    colorPrimary: '#030213',
    colorInfo: '#030213',
    borderRadius: 10,
    colorBgLayout: '#fafafa',
    colorBgContainer: '#ffffff',
    colorText: '#171717',
    fontSize: 14,
    wireframe: false,
  },
  components: {
    Layout: {
      siderBg: '#ffffff',
      headerBg: '#ffffff',
    },
    Menu: {
      itemBg: '#ffffff',
      itemColor: '#525252',
      itemSelectedBg: '#f5f5f5',
      itemSelectedColor: '#171717',
      itemHoverColor: '#171717',
    },
    Card: {
      borderRadiusLG: 10,
    },
  },
}
