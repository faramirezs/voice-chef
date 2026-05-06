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
import { ArrowRight01Icon, ReceiptEuroIcon } from "@hugeicons/core-free-icons"
import { NavLink } from "react-router-dom"

import { ComputerTerminalIcon } from "@hugeicons/core-free-icons"

const NAV_ITEMS = [
	{
		title: "Starting page",
		url: "/",
		icon: (
			<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
		)
	},
	{
		title: "Recipes",
		url: "/recipes",
		icon: (
			<HugeiconsIcon icon={ReceiptEuroIcon} strokeWidth={2} />
		)
	},
	{
		title: "Menu planner",
		url: "/menu-planner",
		icon: (
			<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
		)
	},
	{
		title: "Tasks",
		url: "/tasks",
		icon: (
			<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
		)
	},
	{
		title: "Calculator",
		url: "/calculator",
		icon: (
			<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
		)
	},
		{
		title: "Timers",
		url: "/timers",
		icon: (
			<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
		)
	},
	{
		title: "Notes",
		url: "/notes",
		icon: (
			<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
		)
	},
		{
		title: "Files",
		url: "/files",
		icon: (
			<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
		)
	},
		{
		title: "Ingredients",
		url: "/ingredients",
		icon: (
			<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
		)
	},
			{
		title: "Analytics",
		url: "/analytics",
		icon: (
			<HugeiconsIcon icon={ComputerTerminalIcon} strokeWidth={2} />
		)
	}
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
