declare module 'lucide-react' {
  import * as React from 'react';
  export interface LucideProps extends React.SVGProps<SVGSVGElement> {
    size?: string | number;
    color?: string;
    strokeWidth?: string | number;
    className?: string;
  }
  export type LucideIcon = React.ForwardRefExoticComponent<LucideProps>;
  export const [key: string]: any;
}

declare module 'echarts-for-react' {
  import * as React from 'react';
  export interface ReactEChartsProps {
    option: any;
    notMerge?: boolean;
    lazyUpdate?: boolean;
    style?: React.CSSProperties;
    className?: string;
    theme?: string | object;
    onEvents?: Record<string, Function>;
    opts?: any;
  }
  export default class ReactECharts extends React.Component<ReactEChartsProps> {}
}

declare module 'maplibre-gl' {
  const maplibregl: any;
  export default maplibregl;
}
