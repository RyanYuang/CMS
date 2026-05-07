import { Avatar, Button, Descriptions, Space, Tag, Typography } from 'antd'
import { PageSectionCard } from '../../components/PageSectionCard'

export function ProfilePage() {
  return (
    <PageSectionCard
      title="Profile"
      description="Personal account profile and security settings."
      extra={<Button type="primary">Edit Profile</Button>}
    >
      <Space direction="vertical" size={16}>
        <Space size={16}>
          <Avatar size={64}>A</Avatar>
          <Space direction="vertical" size={0}>
            <Typography.Title level={5} className="m-0">
              Admin User
            </Typography.Title>
            <Typography.Text type="secondary">admin@leowong.com</Typography.Text>
            <Tag color="blue">Super Admin</Tag>
          </Space>
        </Space>
        <Descriptions bordered column={1}>
          <Descriptions.Item label="Department">Platform Operations</Descriptions.Item>
          <Descriptions.Item label="Last Login">2026-05-08 13:42</Descriptions.Item>
          <Descriptions.Item label="2FA">Enabled</Descriptions.Item>
        </Descriptions>
      </Space>
    </PageSectionCard>
  )
}
