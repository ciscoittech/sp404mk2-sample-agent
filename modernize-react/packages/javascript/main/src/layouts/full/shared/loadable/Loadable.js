import React, { Suspense } from "react";
import Spinner from "../../../../views/spinner/Spinner";

const Loadable = (Component) => (props) =>
  (
    <Suspense fallback={<Spinner />}>
      <Component {...props} />
    </Suspense>
  );

export default Loadable;
