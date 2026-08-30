function Badge({ tone = "neutral", className = "", children, ...rest }) {
  const classes = ["ui-badge", `ui-badge--${tone}`, className]
    .filter(Boolean)
    .join(" ");

  return (
    <span className={classes} {...rest}>
      {children}
    </span>
  );
}

export default Badge;
