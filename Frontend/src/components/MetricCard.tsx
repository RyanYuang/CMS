import { Card, Statistic } from 'antd'
import type { ReactNode } from 'react'

type MetricCardProps = {
  title: string
  value: number | string
  prefix?: ReactNode
  suffix?: string
}

export function MetricCard(props: MetricCardProps) {
  const { title, value, prefix, suffix } = props
  return (
    <Card className="cms-card metric-card">
      <Statistic title={title} value={value} prefix={prefix} suffix={suffix} />
    </Card>
  )
}
