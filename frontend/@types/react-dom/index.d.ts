declare module "react-dom" {
  export * from "react";
}

declare module "react-dom/client" {
  export function createRoot(container: Element | DocumentFragment): {
    render(children: React.ReactNode): void;
    unmount(): void;
  };

  export function hydrateRoot(
    container: Element | DocumentFragment,
    initialChildren: React.ReactNode,
  ): {
    render(children: React.ReactNode): void;
    unmount(): void;
  };
}
