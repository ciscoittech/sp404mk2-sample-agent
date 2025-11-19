import CodeDialog from '../../../shared/CodeDialog';

const SelectCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { useFormik } from 'formik';
import * as yup from 'yup';
import { styled } from '@mui/material/styles';
import { Typography } from '@mui/material';
import { Select } from '@mui/material';

import { Box, Button, Stack, FormHelperText, MenuItem } from '@mui/material';

const CustomFormLabel = styled((props: any) => (
  <Typography
    variant="subtitle1"
    fontWeight={600}
    {...props}
    component="label"
    htmlFor={props.htmlFor}
  />
))(() => ({
  marginBottom: '5px',
  marginTop: '25px',
  display: 'block',
}));

const CustomSelect = styled((props: any) => <Select {...props} />)(({}) => ({}));

const validationSchema = yup.object({
  age: yup.number().required('Age selection is required.'),
});

const formik = useFormik({
        initialValues: {
            age: ''
        },
        validationSchema,
    });

<form onSubmit={formik.handleSubmit}>
    <Stack>
        <Box mt="-10px" mb={3}>
          <CustomFormLabel>Age</CustomFormLabel>
          <CustomSelect
            labelId="age-select"
            id="age"
            fullWidth
            name="age"
            value={formik.values.age}
            onChange={formik.handleChange}
          >
            <MenuItem value="">
              <em>None</em>
            </MenuItem>
            <MenuItem value={10}>Ten</MenuItem>
            <MenuItem value={20}>Twenty</MenuItem>
            <MenuItem value={30}>Thirty</MenuItem>
          </CustomSelect>
          {formik.errors.age && (
            <FormHelperText error id="standard-weight-helper-text-email-login">
              {' '}
              {formik.errors.age}{' '}
            </FormHelperText>
          )}
        </Box>
        <Stack direction="row" justifyContent="flex-end">
          <Button variant="contained" type="submit">
            Submit
          </Button>
        </Stack>
    </Stack>
</form>
`}
      </CodeDialog>
    </>
  );
};

export default SelectCode;
