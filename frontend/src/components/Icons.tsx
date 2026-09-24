import type { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

const defaults: IconProps = {
  width: 20,
  height: 20,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
};

export const AgentNetworkIcon = (props: IconProps) => (
  <svg {...defaults} {...props} viewBox="0 0 24 24">
    <path d="M12 8.5V5.8M8.9 14.1l-2.7 1.6M15.1 14.1l2.7 1.6" />
    <circle cx="12" cy="12" r="3.5" />
    <circle cx="12" cy="3.5" r="2" />
    <circle cx="4.3" cy="17" r="2" />
    <circle cx="19.7" cy="17" r="2" />
    <path d="m10.7 12 1 1 1.8-2" />
  </svg>
);

export const SparkIcon = (props: IconProps) => (
  <svg {...defaults} {...props}><path d="m12 3-1.3 4.3a5 5 0 0 1-3.4 3.4L3 12l4.3 1.3a5 5 0 0 1 3.4 3.4L12 21l1.3-4.3a5 5 0 0 1 3.4-3.4L21 12l-4.3-1.3a5 5 0 0 1-3.4-3.4L12 3Z" /></svg>
);

export const SendIcon = (props: IconProps) => (
  <svg {...defaults} {...props}><path d="m22 2-7 20-4-9-9-4Z" /><path d="M22 2 11 13" /></svg>
);

export const UploadIcon = (props: IconProps) => (
  <svg {...defaults} {...props}><path d="M12 16V4" /><path d="m7 9 5-5 5 5" /><path d="M20 15v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-4" /></svg>
);

export const ShieldIcon = (props: IconProps) => (
  <svg {...defaults} {...props}><path d="M20 13c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V5l8-3 8 3Z" /><path d="m9 12 2 2 4-4" /></svg>
);

export const FileIcon = (props: IconProps) => (
  <svg {...defaults} {...props}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" /><path d="M14 2v6h6" /></svg>
);

export const LogoutIcon = (props: IconProps) => (
  <svg {...defaults} {...props}><path d="M10 17l5-5-5-5" /><path d="M15 12H3" /><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" /></svg>
);

export const PlusIcon = (props: IconProps) => (
  <svg {...defaults} {...props}><path d="M12 5v14M5 12h14" /></svg>
);

export const LockIcon = (props: IconProps) => (
  <svg {...defaults} {...props}><rect width="16" height="11" x="4" y="11" rx="2" /><path d="M8 11V7a4 4 0 0 1 8 0v4" /></svg>
);
