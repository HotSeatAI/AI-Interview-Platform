function Card({
  as: Component = "div",
  variant = "default",
  className = "",
  children,
  ...rest
}) {
  const classes = [
    "ui-card",
    variant !== "default" ? `ui-card--${variant}` : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <Component className={classes} {...rest}>
      {children}
    </Component>
  );
}

export default Card;
