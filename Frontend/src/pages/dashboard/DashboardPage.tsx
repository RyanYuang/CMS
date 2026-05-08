import { ClockCircleOutlined, ExportOutlined, LinkOutlined, PictureOutlined } from '@ant-design/icons'
import { Card, Col, Row, Space, Spin, Typography } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { auditApi, assetsApi, articlesApi, linksApi } from '../../services'
import { formatDate, formatRelativeTime } from '../../utils/format'

export function DashboardPage() {
  const [loading, setLoading] = useState(true)
  const [linkTotal, setLinkTotal] = useState(0)
  const [onlineTotal, setOnlineTotal] = useState(0)
  const [assetTotal, setAssetTotal] = useState(0)
  const [latestTime, setLatestTime] = useState<string>('-')
  const [activities, setActivities] = useState<
    { id: number; actor: string; summary: string; created_at: string }[]
  >([])

  useEffect(() => {
    Promise.all([
      articlesApi.list({ page: 1, page_size: 1 }),
      linksApi.list(),
      assetsApi.list({ page: 1, page_size: 1 }),
      auditApi.list({ page: 1, page_size: 5 }),
    ])
      .then(([articleResult, links, assetsResult, auditResult]) => {
        setLinkTotal(links.length)
        setOnlineTotal(links.filter((item) => item.status === 'online').length)
        setAssetTotal(assetsResult.meta.total)
        const allTimes = [
          ...links.map((item) => item.updated_at),
          ...auditResult.items.map((item) => item.created_at),
          ...articleResult.items.map((item) => item.updated_at),
        ].filter(Boolean)
        const latest = allTimes.sort((a, b) => new Date(b).getTime() - new Date(a).getTime())[0]
        setLatestTime(latest ? formatDate(latest).split(' ')[0] : '-')
        setActivities(
          auditResult.items.map((item) => ({
            id: item.id,
            actor: item.actor_username || '系统',
            summary: item.summary || `${item.action} ${item.target_type}`,
            created_at: item.created_at,
          })),
        )
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  const stats = useMemo(
    () => [
      { title: '链接总数', value: String(linkTotal), icon: <LinkOutlined />, description: '已创建的外链总数' },
      { title: '已上线', value: String(onlineTotal), icon: <ExportOutlined />, description: '当前可访问的链接' },
      { title: '媒体文件', value: String(assetTotal), icon: <PictureOutlined />, description: '图片和视频总数' },
      {
        title: '最近更新',
        value: latestTime,
        icon: <ClockCircleOutlined />,
        description: '最后操作时间',
      },
    ],
    [assetTotal, latestTime, linkTotal, onlineTotal],
  )

  return (
    <Space direction="vertical" size={24} className="w-full">
      <div>
        <Typography.Title level={1} style={{ fontSize: 30, marginBottom: 8 }}>
          仪表盘
        </Typography.Title>
        <Typography.Text type="secondary">查看站点概况和最近活动</Typography.Text>
      </div>
      {loading ? <Spin /> : null}
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
          {activities.map((activity) => (
            <div
              key={activity.id}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                borderBottom: '1px solid #f5f5f5',
                paddingBottom: 12,
              }}
            >
              <Space direction="vertical" size={2}>
                <Typography.Text strong>{activity.actor}</Typography.Text>
                <Typography.Text type="secondary">{activity.summary}</Typography.Text>
              </Space>
              <Typography.Text type="secondary">{formatRelativeTime(activity.created_at)}</Typography.Text>
            </div>
          ))}
        </Space>
      </Card>
    </Space>
  )
}
