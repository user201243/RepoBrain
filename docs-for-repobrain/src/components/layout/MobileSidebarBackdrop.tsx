type MobileSidebarBackdropProps = {
  label: string
  onClose: () => void
}

export function MobileSidebarBackdrop({ label, onClose }: MobileSidebarBackdropProps) {
  return (
    <button
      className="docs-sidebar-backdrop mobile-only"
      type="button"
      aria-label={label}
      onClick={onClose}
    />
  )
}
