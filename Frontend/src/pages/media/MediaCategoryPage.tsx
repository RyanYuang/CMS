import { Card, Col, Row, Typography } from 'antd'
import { useMemo } from 'react'
import { useLocation } from 'react-router-dom'

const categoryMeta: Record<string, { title: string; description: string }> = {
  photos: { title: '照片', description: '管理图片和摄影资源' },
  movies: { title: '电影', description: '管理视频与影片文件' },
  music: { title: '音乐', description: '管理音频与音乐资源' },
  notes: { title: '笔记', description: '管理文档与笔记内容' },
}

export function MediaCategoryPage() {
  const location = useLocation()
  const category = useMemo(() => location.pathname.split('/').at(-1) ?? 'photos', [location.pathname])
  const meta = categoryMeta[category] ?? categoryMeta.photos

  return (
    <Row gutter={[16, 16]}>
      <Col span={24}>
        <Card className="cms-card">
          <Typography.Title level={3}>{meta.title}管理</Typography.Title>
          <Typography.Paragraph type="secondary">{meta.description}</Typography.Paragraph>
        </Card>
      </Col>
      {[1, 2, 3, 4].map((item) => (
        <Col xs={24} md={12} xl={6} key={item}>
          <Card hoverable className="cms-card">
            <Typography.Text strong>{meta.title}资源 #{item}</Typography.Text>
            <Typography.Paragraph type="secondary" className="m-0">
              来自 Figma Media 子页面结构
            </Typography.Paragraph>
          </Card>
        </Col>
      ))}
    </Row>
  )
}
