import { Avatar, Descriptions, Space, Spin, Tag, Typography } from 'antd'
import { useEffect, useState } from 'react'
import { PageSectionCard } from '../../components/PageSectionCard'
import { authApi } from '../../services'
import type { MeResponse } from '../../services'

export function ProfilePage() {
  const [profile, setProfile] = useState<MeResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    authApi
      .me()
      .then((resp) => setProfile(resp))
      .finally(() => setLoading(false))
  }, [])

  return (
    <PageSectionCard
      title="Profile"
      description="Personal account profile and security settings."
    >
      {loading ? <Spin /> : null}
      <Space direction="vertical" size={16}>
        <Space size={16}>
          <Avatar size={64} src={profile?.avatar_url ?? undefined}>
            {profile?.username?.slice(0, 1).toUpperCase()}
          </Avatar>
          <Space direction="vertical" size={0}>
            <Typography.Title level={5} className="m-0">
              {profile?.full_name || profile?.username || '-'}
            </Typography.Title>
            <Typography.Text type="secondary">{profile?.email || '-'}</Typography.Text>
            <Tag color="blue">{profile?.role || 'No Role'}</Tag>
          </Space>
        </Space>
        <Descriptions bordered column={1}>
          <Descriptions.Item label="Username">{profile?.username || '-'}</Descriptions.Item>
          <Descriptions.Item label="Role">{profile?.role || '-'}</Descriptions.Item>
          <Descriptions.Item label="Last Login">以后端用户列表页信息为准</Descriptions.Item>
          <Descriptions.Item label="Permissions">
            <Space wrap>
              {(profile?.permissions || []).map((item) => (
                <Tag key={item}>{item}</Tag>
              ))}
            </Space>
          </Descriptions.Item>
        </Descriptions>
      </Space>
    </PageSectionCard>
  )
}
