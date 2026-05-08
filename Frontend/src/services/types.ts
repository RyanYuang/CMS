export type PageMeta = {
  page: number
  page_size: number
  total: number
  total_pages: number
}

export type PageResult<T> = {
  items: T[]
  meta: PageMeta
}

export type OkResponse = {
  ok: boolean
  message: string
}

export type LoginRequest = {
  username: string
  password: string
}

export type LoginResponse = {
  access_token: string
  token_type: string
  expires_in_minutes: number
}

export type MeResponse = {
  id: number
  username: string
  email: string
  full_name: string | null
  avatar_url: string | null
  role: string | null
  permissions: string[]
}

export type ArticleStatus = 'draft' | 'published' | 'archived'

export type ArticleCreate = {
  title: string
  slug?: string | null
  summary?: string | null
  content: string
  category_id?: number | null
  cover_asset_id?: number | null
  tag_ids?: number[]
  status?: ArticleStatus
}

export type ArticleUpdate = {
  title?: string | null
  slug?: string | null
  summary?: string | null
  content?: string | null
  category_id?: number | null
  cover_asset_id?: number | null
  tag_ids?: number[] | null
  note?: string | null
}

export type ArticleStatusUpdate = {
  status: ArticleStatus
  note?: string | null
}

export type AssetMini = {
  id: number
  public_url: string
}

export type Category = {
  id: number
  name: string
  slug: string
  description: string | null
  parent_id: number | null
  sort_order: number
}

export type Tag = {
  id: number
  name: string
  slug: string
}

export type AuthorMini = {
  id: number
  username: string
  full_name: string | null
}

export type ArticleListItem = {
  id: number
  title: string
  slug: string
  summary: string | null
  status: ArticleStatus
  published_at: string | null
  cover: AssetMini | null
  category: Pick<Category, 'id' | 'name' | 'slug'> | null
  author: AuthorMini | null
  tags: Tag[]
  view_count: number
  current_version: number
  created_at: string
  updated_at: string
}

export type ArticleDetail = ArticleListItem & {
  content: string
}

export type ArticleVersionOut = {
  id: number
  article_id: number
  version: number
  title: string
  slug: string
  summary: string | null
  status: ArticleStatus
  note: string | null
  operator_id: number | null
  created_at: string
}

export type LinkStatus = 'online' | 'offline'

export type LinkItem = {
  id: number
  title: string
  url: string
  cover: string | null
  sort_order: number
  status: LinkStatus
  updated_at: string
}

export type LinkCreate = {
  title: string
  url: string
  cover?: string | null
  sort_order?: number
  status?: LinkStatus
}

export type LinkUpdate = Partial<LinkCreate>

export type AssetKind = 'image' | 'video' | 'audio' | 'document' | 'other'

export type AssetItem = {
  id: number
  filename: string
  public_url: string
  kind: AssetKind
  mime_type: string
  size_bytes: number
  width: number | null
  height: number | null
  is_orphan: boolean
  uploader_id: number | null
  created_at: string
}

export type Permission = {
  id: number
  code: string
  description: string | null
}

export type Role = {
  id: number
  name: string
  description: string | null
  is_builtin: boolean
  permissions: Permission[]
  member_count: number
}

export type RoleCreate = {
  name: string
  description?: string | null
  permission_codes: string[]
}

export type RoleUpdate = {
  description?: string | null
  permission_codes?: string[] | null
}

export type UserRole = {
  id: number
  name: string
}

export type UserItem = {
  id: number
  username: string
  email: string
  full_name: string | null
  is_active: boolean
  avatar_url: string | null
  role: UserRole | null
  last_login_at: string | null
  created_at: string
  updated_at: string
}

export type UserCreate = {
  username: string
  email: string
  password: string
  full_name?: string | null
  role_id?: number | null
  is_active?: boolean
}

export type UserUpdate = {
  email?: string | null
  password?: string | null
  full_name?: string | null
  role_id?: number | null
  is_active?: boolean | null
  avatar_url?: string | null
}

export type AuditAction =
  | 'login'
  | 'logout'
  | 'create'
  | 'update'
  | 'delete'
  | 'publish'
  | 'unpublish'
  | 'archive'
  | 'rollback'
  | 'upload'

export type AuditLog = {
  id: number
  actor_id: number | null
  actor_username: string | null
  action: AuditAction
  target_type: string
  target_id: string | null
  summary: string | null
  diff: Record<string, unknown> | null
  request_ip: string | null
  created_at: string
}

export type SettingItem = {
  key: string
  value: unknown
}

export type CategoryCreate = {
  name: string
  slug?: string | null
  description?: string | null
  parent_id?: number | null
  sort_order?: number
}

export type CategoryUpdate = Partial<CategoryCreate>

export type TagCreate = {
  name: string
  slug?: string | null
}

export type Note = {
  id: number
  title: string
  content: string
  category: string | null
  pinned: boolean
  tags: string[]
  owner_id: number | null
  created_at: string
  updated_at: string
}

export type NoteCreate = {
  title: string
  content?: string
  category?: string | null
  pinned?: boolean
  tags?: string[]
}

export type NoteUpdate = Partial<NoteCreate>

export type NoteCount = {
  total: number
}

export type NoteListQuery = {
  keyword?: string
  category?: string
  page?: number
  page_size?: number
}
