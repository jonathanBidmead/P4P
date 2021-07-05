clear;
r1 = 1;
r2 = 2;
r3 = 2;
r4 = 1;
r5 = 0.5;
r6 = 0;
N = 361;
Axes = 5;


theta2 = getAxisValues();
theta = theta2(1:360,:);
% theta(:,5) = 90;
%converting to my co-ord system
theta(:,2) = theta(:,2) + 90;
%padding
for i = size(theta,1)+1:N
    theta(i,:) = theta(size(theta,1),:);
end


points = zeros(N,Axes+1,3);

%endpoint of first axis
points(:,2,1) = r1.*sind(theta(:,1));%x
points(:,2,2) = r1.*cosd(theta(:,1));%y
points(:,2,3) = 0;%z

r2prime = zeros(N,1);
r2prime(:,1) = r2.*sind(theta(:,2));

%second axis
points(:,3,1) = points(:,2,1) + r2prime.*sind(theta(:,1));%x
points(:,3,2) = points(:,2,2) + r2prime.*cosd(theta(:,1));%y
points(:,3,3) = r2.*cosd(theta(:,2));%z

%third axis
r3prime = zeros(N,1);
r3prime(:,1) = r3.*sind(theta(:,3));

points(:,4,1) = points(:,3,1) + r3prime.*sind(theta(:,1));%x
points(:,4,2) = points(:,3,2) + r3prime.*cosd(theta(:,1));%y
points(:,4,3) = points(:,3,3) + r3.*cosd(theta(:,2)+90) + r3.*cosd(theta(:,3));%z

%fourth axis
r4prime = zeros(N,1);
r4prime(:,1) = r4.*sind(theta(:,3));
points(:,5,1) = points(:,4,1) + r4prime.*sind(theta(:,1));
points(:,5,2) = points(:,4,2) + r4prime.*cosd(theta(:,1));
points(:,5,3) = points(:,4,3) + r4.*cosd(theta(:,2)+90) + r4.*cosd(theta(:,3));

%fifth axis WIP WIP WIP WIP
r5prime = zeros(N,1);
r5prime(:,1) = r5.*sind(theta(:,3));
points(:,6,1) = points(:,5,1) + r5prime.*sind(theta(:,1)) + r5.*sind(theta(:,4)).*cosd(theta(:,5));
points(:,6,2) = points(:,5,2) + r5prime.*cosd(theta(:,1)) + r5.*cosd(theta(:,4)).*cosd(theta(:,5));
points(:,6,3) = points(:,5,3) + r5.*cosd(theta(:,2)+90+theta(:,3))+r5.*cosd(theta(:,4).*sind(theta(:,5)));
% points(:,6,1) = points(:,5,1) + r5.*sind(theta(:,1)).*sind(theta(:,4));
% points(:,6,2) = points(:,5,2) + r5.*cosd(theta(:,1)).*cosd(theta(:,4));
% points(:,6,3) = points(:,5,3) + r5.*cosd(theta(:,2)+90+theta(:,3)+theta(:,5)).*sind(theta(:,4));


h = animatedline('MaximumNumPoints',Axes+1);
hold on
view(3);
axis([-8,8,-8,8,-8,8]);
xlabel('x');
ylabel('y');
zlabel('z');
for i = 1:N
    pts = 1:Axes+1;
%     pts = 1:6;
    addpoints(h,points(i,pts,1),points(i,pts,2),points(i,pts,3));
    drawnow;
    pause(0.01);
end


