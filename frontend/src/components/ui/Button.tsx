import type { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost";
};

export default function Button({
  variant = "ghost",
  className = "",
  ...props
}: Props) {
  const cls = ["btn", variant === "primary" ? "btnPrimary" : "", className]
    .join(" ")
    .trim();

  return <button className={cls} {...props} />;
}