import CodeDialog from 'src/components/shared/CodeDialog';
const Heading2Code = () => {
  return (
    <>
      <CodeDialog>
        {`

import { Typography } from '@mui/material';

<Typography variant="h2">h2. Heading</Typography>`}
      </CodeDialog>
    </>
  );
};

export default Heading2Code;
