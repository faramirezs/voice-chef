"use client"

import * as React from "react"

import { NavMain } from "@/components/nav-main"
import { NavShortcuts } from "@/components/nav-shortcuts"
import { NavUser } from "@/components/nav-user"
import { TeamSwitcher } from "@/components/team-switcher"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar"
import { HugeiconsIcon } from "@hugeicons/react"
import { LayoutBottomIcon, AudioWave01Icon, CommandIcon, RoboticIcon, BookOpen02Icon, Settings05Icon, CropIcon, PieChartIcon, MapsIcon } from "@hugeicons/core-free-icons"

// This is sample data.
const data = {
  // user: {
  //   name: "user",
  //   email: "m@example.com",
  //   avatar: "/avatars/shadcn.jpg",
  // },
  teams: [
    {
      name: "Kitchen Inc",
      logo: (
        <HugeiconsIcon icon={LayoutBottomIcon} strokeWidth={2} />
      ),
      plan: "Enterprise",
    },
  ],
  navMain: [
    // {
    //   title: "AI Assistant",
    //   url: "#",
    //   icon: (
    //     <HugeiconsIcon icon={RoboticIcon} strokeWidth={2} />
    //   ),
    //   items: [
    //     {
    //       title: "Genesis",
    //       url: "#",
    //     },
    //     {
    //       title: "Explorer",
    //       url: "#",
    //     },
    //     {
    //       title: "Quantum",
    //       url: "#",
    //     },
    //   ],
    // },
    // {
    //   title: "Documentation",
    //   url: "#",
    //   icon: (
    //     <HugeiconsIcon icon={BookOpen02Icon} strokeWidth={2} />
    //   ),
    //   items: [
    //     {
    //       title: "Introduction",
    //       url: "#",
    //     },
    //     {
    //       title: "Get Started",
    //       url: "#",
    //     },
    //     {
    //       title: "Tutorials",
    //       url: "#",
    //     },
    //     {
    //       title: "Changelog",
    //       url: "#",
    //     },
    //   ],
    // },
    // {
    //   title: "Settings",
    //   url: "#",
    //   icon: (
    //     <HugeiconsIcon icon={Settings05Icon} strokeWidth={2} />
    //   ),
    //   items: [
    //     {
    //       title: "General",
    //       url: "/settings/",
    //     },
    //     {
    //       title: "Team",
    //       url: "#",
    //     },
    //     {
    //       title: "Billing",
    //       url: "#",
    //     },
    //     {
    //       title: "Limits",
    //       url: "#",
    //     },
    //   ],
    // },
  ],
  shortcuts: [
    // {
    //   name: "Mozarella Sticks",
    //   url: "#",
    //   icon: (
    //     <HugeiconsIcon icon={CropIcon} strokeWidth={2} />
    //   ),
    // },
    // {
    //   name: "Mashed Potatoes",
    //   url: "#",
    //   icon: (
    //     <HugeiconsIcon icon={PieChartIcon} strokeWidth={2} />
    //   ),
    // },
    // {
    //   name: "New York Cheesecake",
    //   url: "#",
    //   icon: (
    //     <HugeiconsIcon icon={MapsIcon} strokeWidth={2} />
    //   ),
    // },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        {/* <TeamSwitcher teams={data.teams} /> */}
      </SidebarHeader>

      <SidebarContent>
        <NavMain items={data.navMain} />
        {/* <NavShortcuts shortcuts={data.shortcuts} /> */}
      </SidebarContent>

      <SidebarFooter>
        <NavUser />
      </SidebarFooter>
      {/* <SidebarRail /> */}
    </Sidebar>
  )
}
