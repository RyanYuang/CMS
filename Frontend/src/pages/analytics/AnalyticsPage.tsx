import { Col, Progress, Row, Space, Table } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { PageSectionCard } from '../../components/PageSectionCard'

type ChannelRow = {
  key: string
  channel: string
  traffic: string
  conversion: string
}

const columns: ColumnsType<ChannelRow> = [
  { title: 'Channel', dataIndex: 'channel' },
  { title: 'Traffic Share', dataIndex: 'traffic' },
  { title: 'Conversion', dataIndex: 'conversion' },
]

const channels: ChannelRow[] = [
  { key: '1', channel: 'Organic Search', traffic: '38%', conversion: '5.2%' },
  { key: '2', channel: 'Paid Ads', traffic: '29%', conversion: '4.4%' },
  { key: '3', channel: 'Referral', traffic: '17%', conversion: '3.8%' },
  { key: '4', channel: 'Social', traffic: '16%', conversion: '2.1%' },
]

export function AnalyticsPage() {
  return (
    <Space direction="vertical" size={20} className="w-full">
      <Row gutter={[16, 16]}>
        <Col xs={24} xl={12}>
          <PageSectionCard title="Campaign Performance">
            <Space direction="vertical" className="w-full">
              <div>Lead Quality <Progress percent={77} /></div>
              <div>Retention <Progress percent={64} /></div>
              <div>Average Session <Progress percent={70} /></div>
            </Space>
          </PageSectionCard>
        </Col>
        <Col xs={24} xl={12}>
          <PageSectionCard title="Traffic Channels">
            <Table columns={columns} dataSource={channels} pagination={false} />
          </PageSectionCard>
        </Col>
      </Row>
    </Space>
  )
}
