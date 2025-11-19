// material
import { TextField, InputAdornment } from '@mui/material';
import { IconSearch } from '@tabler/icons-react';


import { ProductContext } from "src/context/EcommerceContext";
import { useContext } from 'react';


// ----------------------------------------------------------------------
export default function ProductSearch() {
  const { searchProducts } = useContext(ProductContext);


  return (<>
    {/* ------------------------------------------- */}
    {/* Sort Button */}
    {/* ------------------------------------------- */}
    <TextField
      id="outlined-search"
      placeholder="Search Product"
      size="small"
      type="search"
      variant="outlined"
      fullWidth
      onChange={(event) => searchProducts(event.target.value)}
      slotProps={{
        input: {
          startAdornment: (
            <InputAdornment position="start">
              <IconSearch size="14" />
            </InputAdornment>
          ),
        }
      }}
    />
  </>);
}
