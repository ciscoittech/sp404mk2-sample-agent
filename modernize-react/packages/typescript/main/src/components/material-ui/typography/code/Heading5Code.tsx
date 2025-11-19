import CodeDialog from 'src/components/shared/CodeDialog';
const Heading5Code = () => {
  return (
    <>
      <CodeDialog>
        {`

import { Typography } from '@mui/material';

<Typography variant="h5">h5. Heading</Typography>`}
      </CodeDialog>
    </>
  );
};

export default Heading5Code;
