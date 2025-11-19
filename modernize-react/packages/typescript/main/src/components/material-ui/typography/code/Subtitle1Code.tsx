import CodeDialog from 'src/components/shared/CodeDialog';
const Subtitle1Code = () => {
  return (
    <>
      <CodeDialog>
        {`

import { Typography } from '@mui/material';

<Typography variant="subtitle1">
    subtitle1. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis
    tenetur
</Typography>`}
      </CodeDialog>
    </>
  );
};

export default Subtitle1Code;
