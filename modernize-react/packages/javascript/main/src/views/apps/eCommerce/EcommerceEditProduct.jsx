import { Button, Grid, Stack } from '@mui/material';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';

import GeneralCard from 'src/components/apps/ecommerce/productEdit/GeneralCard';
import MediaCard from 'src/components/apps/ecommerce/productEdit/Media';
import VariationCard from 'src/components/apps/ecommerce/productEdit/VariationCard';
import PricingCard from 'src/components/apps/ecommerce/productEdit/Pricing';
import Thumbnail from 'src/components/apps/ecommerce/productEdit/Thumbnail';
import StatusCard from 'src/components/apps/ecommerce/productEdit/Status';
import ProductDetails from 'src/components/apps/ecommerce/productEdit/ProductDetails';
import ProductTemplate from 'src/components/apps/ecommerce/productEdit/ProductTemplate';
import CustomersReviews from 'src/components/apps/ecommerce/productEdit/CustomersReviews';
import ProductAvgSales from 'src/components/apps/ecommerce/productEdit/ProductAvgSales';
import BlankCard from 'src/components/shared/BlankCard';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Edit Product',
  },
];

const EcommerceEditProduct = () => {
  return (
    <PageContainer title="Edit Product" description="this is Edit Product">
      {/* breadcrumb */}
      <Breadcrumb title="Edit Product" items={BCrumb} />
      <form>
        <Grid container spacing={3}>
          <Grid
            size={{
              lg: 8
            }}>
            <Stack spacing={3}>
              <BlankCard>
                <GeneralCard />
              </BlankCard>

              <BlankCard>
                <MediaCard />
              </BlankCard>

              <BlankCard>
                <VariationCard />
              </BlankCard>

              <BlankCard>
                <PricingCard />
              </BlankCard>

              <BlankCard>
                <CustomersReviews />
              </BlankCard>
            </Stack>
          </Grid>

          <Grid
            size={{
              lg: 4
            }}>
            <Stack spacing={3}>
              <BlankCard>
                <Thumbnail />
              </BlankCard>

              <BlankCard>
                <StatusCard />
              </BlankCard>

              <BlankCard>
                <ProductDetails />
              </BlankCard>

              <BlankCard>
                <ProductAvgSales />
              </BlankCard>

              <BlankCard>
                <ProductTemplate />
              </BlankCard>
            </Stack>
          </Grid>
        </Grid>

        <Stack direction="row" spacing={2} mt={3}>
          <Button variant="contained" color="primary">
            Save Changes
          </Button>
          <Button variant="outlined" color="error">
            Cancel
          </Button>
        </Stack>
      </form>
    </PageContainer>
  );
};

export default EcommerceEditProduct;
