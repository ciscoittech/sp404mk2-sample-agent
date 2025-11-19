import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import { InvoiceProvider } from 'src/context/InvoiceContext/index';
import InvoiceDetail from 'src/components/apps/invoice/Invoice-detail/index';
import BlankCard from 'src/components/shared/BlankCard';
import { CardContent } from '@mui/material';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Invoice Details',
  },
];

const InvoiceDetailPage = () => {
  return (
    <InvoiceProvider>
      <PageContainer title="Invoice Detail" description="this is Invoice Detail">
        <Breadcrumb title="Invoice Detail" items={BCrumb} />
        <BlankCard>
          <CardContent>
            <InvoiceDetail />
          </CardContent>
        </BlankCard>
      </PageContainer>
    </InvoiceProvider>
  );
};
export default InvoiceDetailPage;
