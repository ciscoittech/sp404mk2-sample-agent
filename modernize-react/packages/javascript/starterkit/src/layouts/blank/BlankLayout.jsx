import { Outlet } from "react-router";
import LoadingBar from '../../LoadingBar';

const BlankLayout = () => (
  <>
    <LoadingBar />
    <Outlet />
  </>
);

export default BlankLayout;
