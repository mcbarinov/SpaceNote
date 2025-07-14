interface UnderConstructionProps {
  title?: string
}

export function UnderConstruction({ title = "Under Construction" }: UnderConstructionProps) {
  return <div className="text-center py-20 text-muted-foreground">🚧 {title}</div>
}