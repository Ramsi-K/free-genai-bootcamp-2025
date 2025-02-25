import { useLocation } from 'react-router-dom'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { useNavigation } from '@/context/NavigationContext'

// Define route mappings for breadcrumbs
const routeMappings: { [key: string]: string } = {
  '': 'Dashboard',
  'dashboard': 'Dashboard',
  'study-activities': 'Study Activities',
  'words': 'Words',
  'groups': 'Word Groups',
  'sessions': 'Study Sessions',
  'settings': 'Settings',
  'launch': 'Launch'
}

export default function Breadcrumbs() {
  const location = useLocation()
  const { currentGroup, currentWord, currentStudyActivity } = useNavigation()
  const pathnames = location.pathname.split('/').filter((x) => x)
  
  // If we're at root, show dashboard
  if (pathnames.length === 0) {
    pathnames.push('')
  }

  const breadcrumbItems = pathnames.map((name, index) => {
    let displayName = routeMappings[name] || name
    
    // Use group, word, or activity name for the last item if available
    if (index === pathnames.length - 1 || (name !== 'launch' && index === pathnames.length - 2)) {
      if (currentGroup && name === currentGroup.id.toString()) {
        displayName = currentGroup.group_name
      } else if (currentWord && name === currentWord.id.toString()) {
        displayName = currentWord.kanji
      } else if (currentStudyActivity && name === currentStudyActivity.id.toString()) {
        displayName = currentStudyActivity.title
      }
    }

    const isLast = index === pathnames.length - 1
    const items = []

    items.push(
      <BreadcrumbItem key={`item-${name || 'home'}`}>
        {isLast ? (
          <BreadcrumbPage>{displayName}</BreadcrumbPage>
        ) : (
          <BreadcrumbLink href={`/${pathnames.slice(0, index + 1).join('/')}`}>
            {displayName}
          </BreadcrumbLink>
        )}
      </BreadcrumbItem>
    )

    if (!isLast) {
      items.push(
        <BreadcrumbSeparator key={`separator-${name || 'home'}`} />
      )
    }

    return items
  }).flat()

  return (
    <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="mr-2 h-4" />
      <Breadcrumb>
        <BreadcrumbList>
          {breadcrumbItems}
        </BreadcrumbList>
      </Breadcrumb>
    </header>
  )
}