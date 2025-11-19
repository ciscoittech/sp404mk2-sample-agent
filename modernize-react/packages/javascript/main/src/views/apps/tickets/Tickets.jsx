import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import TicketListing from 'src/components/apps/tickets/TicketListing';
import TicketFilter from 'src/components/apps/tickets/TicketFilter';
import ChildCard from 'src/components/shared/ChildCard';
import { TicketProvider } from 'src/context/TicketContext';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Tickets',
  },
];

const TicketList = () => {
  return (
    <TicketProvider>
      <PageContainer title="Tickets App" description="this is Note page">
        <Breadcrumb title="Tickets app" items={BCrumb} />
        <ChildCard>
          <TicketFilter />
          <TicketListing />
        </ChildCard>
      </PageContainer>
    </TicketProvider>
  );
};

export default TicketList;
