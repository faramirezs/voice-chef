import * as React from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"

export interface ComboboxOption {
  value: string
  label: string
}

interface ComboboxProps {
  options: ComboboxOption[]
  value?: string
  onValueChange?: (value: string) => void
  placeholder?: string
  searchPlaceholder?: string
  emptyText?: string
  isLoading?: boolean
  onSearchChange?: (search: string) => void
}

export function Combobox({
  options,
  value,
  onValueChange,
  placeholder = "Select option...",
  searchPlaceholder = "Search...",
  emptyText = "No options found.",
  isLoading = false,
  onSearchChange,
}: ComboboxProps) {
  const [open, setOpen] = React.useState(false)
  const [search, setSearch] = React.useState("")

  const selectedLabel = options.find((opt) => opt.value === value)?.label || placeholder

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newSearch = e.target.value
    setSearch(newSearch)
    onSearchChange?.(newSearch)
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            "w-full justify-start h-9 border-black",
            !value && "text-muted-foreground"
          )}
        >
          <span className="truncate">{selectedLabel}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-2" align="start">
        <div className="space-y-2 w-full">
          <Input
            placeholder={searchPlaceholder}
            value={search}
            onChange={handleSearchChange}
            className="h-8 w-full"
          />
          <div className="max-h-48 overflow-y-auto">
            {isLoading && (
              <div className="p-2 text-sm text-muted-foreground">Loading...</div>
            )}
            {!isLoading && options.length === 0 && (
              <div className="p-2 text-sm text-muted-foreground">{emptyText}</div>
            )}
            {!isLoading && options.length > 0 && (
              <ul>
                {options.map((option) => (
                  <li
                    key={option.value}
                    onClick={() => {
                      onValueChange?.(option.value)
                      setOpen(false)
                      setSearch("")
                    }}
                    className="px-3 py-2 hover:bg-accent cursor-pointer text-sm rounded"
                  >
                    {option.label}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  )
}
