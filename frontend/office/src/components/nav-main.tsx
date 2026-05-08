import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import type * as React from "react"
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar"
import { HugeiconsIcon } from "@hugeicons/react"
import { ArrowRight01Icon, Calendar03Icon, ComponentIcon, CookBookIcon, Files01Icon, Home07Icon, RoboticIcon, Key01Icon } from "@hugeicons/core-free-icons"
import { NavLink } from "react-router-dom"


const NAV_ITEMS = [
	{
		title: "Starting page",
		url: "/",
		icon: (
			<HugeiconsIcon icon={Home07Icon} strokeWidth={2} />
		)
	},
	{
		title: "Recipes",
		url: "/recipes",
		icon: (
			<HugeiconsIcon icon={CookBookIcon} strokeWidth={2} />
		)
	},
	{
		title: "Menu planner",
		url: "/menu-planner",
		icon: (
			<HugeiconsIcon icon={Calendar03Icon} strokeWidth={2} />
		)
	},
	// {
	// 	title: "Tasks",
	// 	url: "/tasks",
	// 	icon: (
	// 		<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
	// 	)
	// },
	// {
	// 	title: "Calculator",
	// 	url: "/calculator",
	// 	icon: (
	// 		<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
	// 	)
	// },
	// {
	// 	title: "Timers",
	// 	url: "/timers",
	// 	icon: (
	// 		<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
	// 	)
	// },
	// {
	// 	title: "Notes",
	// 	url: "/notes",
	// 	icon: (
	// 		<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
	// 	)
	// },
	{
		title: "Files",
		url: "/files",
		icon: (
			<HugeiconsIcon icon={Files01Icon} strokeWidth={2} />
		)
	},
	{
		title: "Ingredients",
		url: "/ingredients",
		icon: (
			<HugeiconsIcon icon={ComponentIcon} strokeWidth={2} />
		)
	},
	{
		title: "AI Assistant",
		url: "/ai-assistant",
		icon: (
			<HugeiconsIcon icon={RoboticIcon} strokeWidth={2} />
		)
	},
	{
		title: "API Keys",
		url: "/api-keys",
		icon: (
			<HugeiconsIcon icon={Key01Icon} strokeWidth={2} />
		)
	},
	// 	{
	// 	title: "Analytics",
	// 	url: "/analytics",
	// 	icon: (
	// 		<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
	// 	)
	// }
]

export function NavMain({
  items,
}: {
  items: {
    title: string
    url: string
    icon?: React.ReactNode
    isActive?: boolean
    items?: {
      title: string
      url: string
    }[]
  }[]
}) {
  return (
    <SidebarGroup>
      <SidebarGroupLabel>Navigation</SidebarGroupLabel>
      <SidebarMenu>
				{NAV_ITEMS.map((item) => (
					<SidebarMenuItem key={item.title}>
							<NavLink to={item.url} className={({ isActive }) => isActive ? "bg-primary/10 text-primary" : ""}>
						<SidebarMenuButton>
								{item.icon}
								<span>{item.title}</span>
						</SidebarMenuButton>
							</NavLink>
					</SidebarMenuItem>
				))}

        {items.map((item) => (
          <Collapsible
            key={item.title}
            asChild
            defaultOpen={item.isActive}
            className="group/collapsible"
          >
            <SidebarMenuItem>
              <CollapsibleTrigger asChild>
                <SidebarMenuButton tooltip={item.title}>
                  {item.icon}
                  <span>{item.title}</span>
                  <HugeiconsIcon icon={ArrowRight01Icon} strokeWidth={2} className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                </SidebarMenuButton>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <SidebarMenuSub>
                  {item.items?.map((subItem) => (
                    <SidebarMenuSubItem key={subItem.title}>
                      <SidebarMenuSubButton asChild>
												<NavLink to={subItem.url} className={({ isActive }) => isActive ? "bg-primary/10 text-primary" : ""}>
                          <span>{subItem.title}</span>
                        </NavLink>
                      </SidebarMenuSubButton>
                    </SidebarMenuSubItem>
                  ))}
                </SidebarMenuSub>
              </CollapsibleContent>
            </SidebarMenuItem>
          </Collapsible>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  )
}
