import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import EditInvoicePage from 'src/components/apps/invoice/Edit-invoice/index';
import { InvoiceProvider } from 'src/context/InvoiceContext/index';
import BlankCard from 'src/components/shared/BlankCard';
import { CardContent } from '@mui/material';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Invoice Edit',
  },
];

const InvoiceEdit = () => {
  return (
    <InvoiceProvider>
      <PageContainer title="Edit Invoice" description="this is Edit Invoice">
        <Breadcrumb title="Edit Invoice" items={BCrumb} />
        <BlankCard>
          <CardContent>
            <EditInvoicePage />
          </CardContent>
        </BlankCard>
      </PageContainer>
    </InvoiceProvider>
  );
};

export default InvoiceEdit;
