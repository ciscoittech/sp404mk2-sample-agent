'use client'

import Autocomplete from '@mui/material/Autocomplete';
import top100Films from './data';
import CustomCheckbox from '../../theme-elements/CustomCheckbox';
import CustomTextField from '../../theme-elements/CustomTextField';



export default function CheckboxesAutocomplete() {
  return (
    <Autocomplete
      multiple
      id="checkboxes-tags-demo"
      options={top100Films}
      disableCloseOnSelect
      getOptionLabel={(option) => option.title}
      renderOption={(props, option, { selected }) => {
        const { key, ...optionProps } = props;
        return (
          <li key={key} {...optionProps}>
            <CustomCheckbox style={{ marginRight: 8 }} checked={selected} />
            {option.title}
          </li>
        );
      }}
      fullWidth
      renderInput={(params) => (
        <CustomTextField {...params} placeholder="Favorites" aria-label="Favorites" />
      )}
    />
  );
}



