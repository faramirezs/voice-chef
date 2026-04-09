import { useMemo, useState } from 'react';
import { Button } from '@/components/ui/button';

const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

function getMonthGrid(baseDate: Date) {
  const year = baseDate.getFullYear();
  const month = baseDate.getMonth();

  const firstOfMonth = new Date(year, month, 1);
  const startDay = (firstOfMonth.getDay() + 6) % 7; // Monday = 0
  const gridStart = new Date(year, month, 1 - startDay);

  return Array.from({ length: 42 }, (_, i) => {
    const date = new Date(gridStart);
    date.setDate(gridStart.getDate() + i);
    return date;
  });
}

export function MenuPlannerPage() {
  const [visibleMonth, setVisibleMonth] = useState(() => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), 1);
  });

  const today = new Date();
  const calendarDays = useMemo(() => getMonthGrid(visibleMonth), [visibleMonth]);

  const monthLabel = visibleMonth.toLocaleDateString(undefined, {
    month: 'long',
    year: 'numeric',
  });

  const goToPreviousMonth = () => {
    setVisibleMonth((current) =>
      new Date(current.getFullYear(), current.getMonth() - 1, 1),
    );
  };

  const goToNextMonth = () => {
    setVisibleMonth((current) =>
      new Date(current.getFullYear(), current.getMonth() + 1, 1),
    );
  };

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold">Menu planner</h1>
        <p className="text-muted-foreground">Plan your meals and production schedule.</p>
      </div>

      <div className="rounded-xl border bg-card p-4 md:p-6">
        <div className="mb-4 flex items-center justify-between gap-2">
          <Button variant="outline" onClick={goToPreviousMonth}>
            Prev
          </Button>
          <h2 className="text-lg font-semibold capitalize">{monthLabel}</h2>
          <Button variant="outline" onClick={goToNextMonth}>
            Next
          </Button>
        </div>

        <div className="grid grid-cols-7 gap-2 text-center text-sm">
          {WEEKDAY_LABELS.map((label) => (
            <div key={label} className="py-2 font-medium text-muted-foreground">
              {label}
            </div>
          ))}

          {calendarDays.map((date) => {
            const isCurrentMonth = date.getMonth() === visibleMonth.getMonth();
            const isToday =
              date.getDate() === today.getDate() &&
              date.getMonth() === today.getMonth() &&
              date.getFullYear() === today.getFullYear();

            return (
              <div
                key={date.toISOString()}
                className={`flex h-24 items-start justify-end rounded-md border p-2 text-sm ${
                  isCurrentMonth
                    ? 'bg-background text-foreground'
                    : 'bg-muted/40 text-muted-foreground'
                } ${isToday ? 'ring-2 ring-primary' : ''}`}
              >
                <span className="font-medium">{date.getDate()}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
