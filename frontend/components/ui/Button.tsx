import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
    extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "ghost";
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = "primary", ...props }, ref) => {
        return (
            <button
                className={cn(
                    variant === "primary" && "button-primary",
                    variant === "secondary" && "inline-flex items-center gap-2 bg-white text-foreground border border-gray-200 rounded-full px-5 py-3 shadow-sm hover:bg-gray-50 transition cursor-pointer",
                    variant === "ghost" && "inline-flex items-center gap-2 text-muted hover:text-foreground transition cursor-pointer",
                    className
                )}
                ref={ref}
                {...props}
            />
        );
    }
);
Button.displayName = "Button";

export { Button };
