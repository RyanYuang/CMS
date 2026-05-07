import { Card, Space, Typography } from 'antd'
import type { ReactNode } from 'react'

type PageSectionCardProps = {
  title: string
  description?: string
  extra?: ReactNode
  children: ReactNode
}

export function PageSectionCard(props: PageSectionCardProps) {
  const { title, description, extra, children } = props
  return (
    <Card className="cms-card" extra={extra}>
      <Space direction="vertical" size={16} className="w-full">
        <Space direction="vertical" size={4}>
          <Typography.Title level={4} className="m-0">
            {title}
          </Typography.Title>
          {description ? (
            <Typography.Text type="secondary">{description}</Typography.Text>
          ) : null}
        </Space>
        {children}
      </Space>
    </Card>
  )
}
