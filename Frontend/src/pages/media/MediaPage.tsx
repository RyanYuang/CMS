import { ArrowRightOutlined, FileTextOutlined, PlaySquareOutlined, SoundOutlined } from '@ant-design/icons'
import { Button, Card, Col, Row, Space, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'

const mediaCategories = [
  { id: 'photos', title: '照片', description: '管理图片和摄影作品', icon: <FileTextOutlined />, count: 156, route: '/media/photos', bg: '#eff6ff', color: '#2563eb' },
  { id: 'movies', title: '电影', description: '管理视频和影片资源', icon: <PlaySquareOutlined />, count: 24, route: '/media/movies', bg: '#f5f3ff', color: '#7c3aed' },
  { id: 'music', title: '音乐', description: '管理音频和音乐文件', icon: <SoundOutlined />, count: 89, route: '/media/music', bg: '#f0fdf4', color: '#16a34a' },
  { id: 'notes', title: '笔记', description: '管理文档和笔记内容', icon: <FileTextOutlined />, count: 42, route: '/media/notes', bg: '#fff7ed', color: '#ea580c' },
]

export function MediaPage() {
  const navigate = useNavigate()

  return (
    <Space direction="vertical" size={24} className="w-full">
      <div>
        <Typography.Title level={1} style={{ fontSize: 30, marginBottom: 8 }}>
          媒体库
        </Typography.Title>
        <Typography.Text type="secondary">管理您的各类媒体资源</Typography.Text>
      </div>
      <Row gutter={[16, 16]}>
        {mediaCategories.map((category) => (
          <Col xs={24} sm={12} lg={6} key={category.id}>
            <Card
              hoverable
              className="cms-card"
              onClick={() => navigate(category.route)}
              styles={{ body: { cursor: 'pointer' } }}
            >
              <Space direction="vertical" size={14} className="w-full">
                <Space className="w-full" style={{ justifyContent: 'space-between' }}>
                  <div style={{ borderRadius: 8, padding: 10, background: category.bg, color: category.color }}>
                    {category.icon}
                  </div>
                  <ArrowRightOutlined style={{ color: '#a3a3a3' }} />
                </Space>
                <Typography.Title level={4} style={{ margin: 0 }}>
                  {category.title}
                </Typography.Title>
                <Typography.Text type="secondary">{category.description}</Typography.Text>
                <Space size={6}>
                  <Typography.Title level={2} style={{ margin: 0 }}>
                    {category.count}
                  </Typography.Title>
                  <Typography.Text type="secondary">个文件</Typography.Text>
                </Space>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
      <Card className="cms-card" style={{ borderStyle: 'dashed' }}>
        <Space className="w-full" style={{ justifyContent: 'space-between' }}>
          <Space direction="vertical" size={2}>
            <Typography.Text strong>快速访问</Typography.Text>
            <Typography.Text type="secondary">点击上方任意分类卡片进入对应的管理界面</Typography.Text>
          </Space>
          <Button onClick={() => navigate('/media/photos')}>前往照片管理</Button>
        </Space>
      </Card>
    </Space>
  )
}
