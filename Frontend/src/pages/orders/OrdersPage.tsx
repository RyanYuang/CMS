import { Empty } from 'antd'
import { PageSectionCard } from '../../components/PageSectionCard'

export function OrdersPage() {
  return (
    <PageSectionCard title="Order Center" description="Track transactions and fulfillment states.">
      <Empty description="该模块尚未启用，敬请期待" />
    </PageSectionCard>
  )
}
