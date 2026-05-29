export type RoutesTypes = Array<
  | {
      component?: string | undefined;
      layout?: false | undefined;
      path?: string | undefined;
      redirect?: string | undefined;
      routes?: RoutesTypes;
      wrappers?: Array<string> | undefined;
    }
  | { [x: string]: any }
>;

const routes: RoutesTypes = [
  {
    path: '/',
    component: './Home',
    layout: false,
  },
  {
    path: '/docs',
    component: './Docs',
    layout: false,
  },
  {
    path: '/traces',
    component: './AgentTrace',
    layout: false,
  },
  {
    path: '/traces/:runId',
    component: './AgentTrace/Detail',
    layout: false,
  },
];

export default routes;
