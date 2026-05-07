import { ClockCircleOutlined, ExportOutlined, LinkOutlined, PictureOutlined } from '@ant-design/icons'
import { Card, Col, Row, Space, Typography } from 'antd'
import { formatDate } from '../../utils/format'

const stats = [
  { title: '链接总数', value: '24', icon: <LinkOutlined />, description: '已创建的外链总数' },
  { title: '已上线', value: '18', icon: <ExportOutlined />, description: '当前可访问的链接' },
  { title: '媒体文件', value: '156', icon: <PictureOutlined />, description: '图片和视频总数' },
  {
    title: '最近更新',
    value: formatDate(new Date()).split(' ')[0],
    icon: <ClockCircleOutlined />,
    description: '最后操作时间',
  },
]

const recentActivities = [
  { action: '新增链接', target: '春季促销活动页', time: '2 小时前' },
  { action: '上传图片', target: 'banner-2024.png', time: '5 小时前' },
  { action: '修改链接', target: '产品介绍页', time: '1 天前' },
  { action: '删除媒体', target: 'old-logo.svg', time: '2 天前' },
  { action: '更新设置', target: '站点名称', time: '3 天前' },
]

export function DashboardPage() {
  return (
    <Space direction="vertical" size={24} className="w-full">
      <div>
        <Typography.Title level={1} style={{ fontSize: 30, marginBottom: 8 }}>
          仪表盘
        </Typography.Title>
        <Typography.Text type="secondary">查看站点概况和最近活动</Typography.Text>
      </div>
      <Row gutter={[16, 16]}>
        {stats.map((stat) => (
          <Col xs={24} md={12} xl={6} key={stat.title}>
            <Card className="cms-card">
              <Space direction="vertical" size={8} className="w-full">
                <Space className="w-full" style={{ justifyContent: 'space-between' }}>
                  <Typography.Text type="secondary">{stat.title}</Typography.Text>
                  {stat.icon}
                </Space>
                <Typography.Title level={2} style={{ margin: 0 }}>
                  {stat.value}
                </Typography.Title>
                <Typography.Text type="secondary">{stat.description}</Typography.Text>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
      <Card className="cms-card">
        <Space direction="vertical" size={16} className="w-full">
          <Typography.Title level={4} style={{ margin: 0 }}>
            最近操作
          </Typography.Title>
          {recentActivities.map((activity) => (
            <div
              key={`${activity.action}-${activity.target}`}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                borderBottom: '1px solid #f5f5f5',
                paddingBottom: 12,
              }}
            >
              <Space direction="vertical" size={2}>
                <Typography.Text strong>{activity.action}</Typography.Text>
                <Typography.Text type="secondary">{activity.target}</Typography.Text>
              </Space>
              <Typography.Text type="secondary">{activity.time}</Typography.Text>
            </div>
          ))}
        </Space>
      </Card>
    </Space>
  )
}
