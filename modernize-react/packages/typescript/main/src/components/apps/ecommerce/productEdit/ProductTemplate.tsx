
import { useState } from 'react';
import Box from '@mui/material/Box';
import { Grid, MenuItem, Typography } from '@mui/material';
import CustomSelect from 'src/components/forms/theme-elements/CustomSelect';
import CustomFormLabel from 'src/components/forms/theme-elements/CustomFormLabel';

const ProductTemplate = () => {
  const [age, setAge] = useState('1');
  const handleChange = (event: any) => {
    setAge(event.target.value);
  };

  return (
    (<Box p={3}>
      <Typography variant="h5" mb={3}>
        Product Template
      </Typography>
      <Grid container spacing={3}>
        <Grid size={12}>
          <CustomFormLabel htmlFor="p_tax" sx={{ mt: 0 }}>
            Select a product template
          </CustomFormLabel>
          <CustomSelect id="p_tax" value={age} onChange={handleChange} fullWidth>
            <MenuItem value={0}>Default Template</MenuItem>
            <MenuItem value={1}>Fashion</MenuItem>
            <MenuItem value={2}>Office Stationary</MenuItem>
            <MenuItem value={3}>Electronics</MenuItem>
          </CustomSelect>
          <Typography variant="body2" mt={1}>
            Assign a template from your current theme to define how a single product is displayed.
          </Typography>
        </Grid>
      </Grid>
    </Box>)
  );
};

export default ProductTemplate;
