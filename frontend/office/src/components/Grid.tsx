export function Grid({ children }: { children: React.ReactNode }) {
  return<div className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-4">{children}
  </div>;
}